import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

interface ResendEmail {
  from: string;
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  text?: string;
  html?: string;
  attachments?: Array<{
    filename: string;
    content_type: string;
    size: number;
    url: string;
  }>;
  message_id?: string;
}

interface EmailRoute {
  workspace_id: string;
  channel_id: string;
  is_direct: boolean;
}

Deno.serve(async (req) => {
  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const inboundMailHost = Deno.env.get("INBOUND_MAIL_HOST")!;

    const supabase = createClient(supabaseUrl, supabaseKey);

    const payload: ResendEmail = await req.json();
    console.log("Received email webhook:", {
      from: payload.from,
      to: payload.to,
      subject: payload.subject,
    });

    const route = await routeEmail(supabase, payload, inboundMailHost);
    if (!route) {
      console.log("Email not routed - invalid destination or sender");
      return new Response(JSON.stringify({ ok: true, skipped: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    const fromMember = await getOrCreateMember(
      supabase,
      route.workspace_id,
      payload.from
    );
    if (!fromMember) {
      console.log("Sender not a workspace member, ignoring email");
      return new Response(JSON.stringify({ ok: true, skipped: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    const { data: message, error: messageError } = await supabase
      .from("messages")
      .insert({
        workspace_id: route.workspace_id,
        channel_id: route.channel_id,
        type: "email",
        from_member_id: fromMember.id,
        status: "processing",
        processing_stage: "saving_message",
        email_message_id: payload.message_id,
        email_subject: payload.subject,
        email_to: payload.to,
        email_cc: payload.cc || [],
        email_bcc: payload.bcc || [],
        email_html: payload.html,
        content_text: payload.text || "",
        content_html: payload.html,
      })
      .select()
      .single();

    if (messageError) {
      console.error("Failed to save message:", messageError);
      throw new Error(`Failed to save message: ${messageError.message}`);
    }

    console.log("Message saved:", message.id);

    if (payload.attachments && payload.attachments.length > 0) {
      const attachmentRecords = payload.attachments.map((att) => ({
        workspace_id: route.workspace_id,
        message_id: message.id,
        filename: att.filename,
        content_type: att.content_type,
        size_bytes: att.size,
        status: "pending",
        metadata: { download_url: att.url },
      }));

      const { error: attachmentError } = await supabase
        .from("attachments")
        .insert(attachmentRecords);

      if (attachmentError) {
        console.error("Failed to save attachments:", attachmentError);
      } else {
        console.log(`Saved ${attachmentRecords.length} attachment records`);
      }
    }

    await supabase
      .from("messages")
      .update({
        status: route.is_direct ? "pending" : "processed",
        processing_stage: route.is_direct
          ? "awaiting_agent_response"
          : "completed",
      })
      .eq("id", message.id);

    if (route.is_direct) {
      const { error: queueError } = await supabase.rpc("pgmq_public.send", {
        queue_name: "incoming-messages",
        message: {
          message_id: message.id,
          workspace_id: route.workspace_id,
          channel_id: route.channel_id,
          action: "generate_response",
        },
      });

      if (queueError) {
        console.error("Failed to enqueue message:", queueError);
      } else {
        console.log("Enqueued message for agent response");
      }
    }

    return new Response(
      JSON.stringify({
        ok: true,
        message_id: message.id,
        is_direct: route.is_direct,
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Error processing webhook:", error);
    return new Response(
      JSON.stringify({
        error: error.message,
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
});

async function routeEmail(
  supabase: any,
  email: ResendEmail,
  inboundMailHost: string
): Promise<EmailRoute | null> {
  const allRecipients = [
    ...email.to,
    ...(email.cc || []),
    ...(email.bcc || []),
  ];

  for (const recipient of allRecipients) {
    const match = recipient.match(/^([^@]+)@([^@]+)$/);
    if (!match) continue;

    const [, user, domain] = match;

    if (!domain.endsWith(inboundMailHost)) continue;

    const subdomain = domain.replace(`.${inboundMailHost}`, "");
    if (subdomain === domain) continue;

    const { data: workspace } = await supabase
      .from("workspaces")
      .select("id")
      .eq("short_name", subdomain)
      .single();

    if (!workspace) continue;

    const { data: channel } = await supabase
      .from("channels")
      .select("id")
      .eq("workspace_id", workspace.id)
      .eq("short_name", user)
      .single();

    if (!channel) continue;

    const is_direct = email.to.includes(recipient);

    return {
      workspace_id: workspace.id,
      channel_id: channel.id,
      is_direct,
    };
  }

  return null;
}

async function getOrCreateMember(
  supabase: any,
  workspace_id: string,
  email: string
): Promise<{ id: string } | null> {
  const { data: profile } = await supabase
    .from("profiles")
    .select("id")
    .eq("email", email)
    .eq("type", "user")
    .single();

  if (!profile) {
    return null;
  }

  const { data: member } = await supabase
    .from("members")
    .select("id")
    .eq("workspace_id", workspace_id)
    .eq("profile_id", profile.id)
    .single();

  return member;
}
