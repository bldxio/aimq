from typing import Any, List
from ..job import Job
from ..clients.supabase import supabase
from .base import QueueProvider, QueueNotFoundError

class SupabaseQueueProvider(QueueProvider):
    """Supabase implementation of QueueProvider."""
    
    def _rpc(self, method: str, params: dict) -> Any:
        """Execute a Supabase RPC call."""
        try:
            result = supabase.client.schema('pgmq_public').rpc(method, params).execute()
            return result.data
        except Exception as e:
            # Check for PostgreSQL error in error message or details
            error_msg = str(e)
            if '42P01' in error_msg:  # Check for table/relation not found error
                raise QueueNotFoundError(f"Queue '{params.get('queue_name')}' does not exist. Please create the queue before using it.")
            raise

    def send(self, queue_name: str, data: dict[str, Any], delay: int | None = None) -> int:
        params = {
            'queue_name': queue_name,
            'message': data
        }
        if delay is not None:
            params['sleep_seconds'] = delay
            
        result = self._rpc('send', params)
        return result[0]

    def send_batch(self, queue_name: str, data_list: list[dict[str, Any]], delay: int | None = None) -> list[int]:
        params = {
            'queue_name': queue_name,
            'messages': data_list
        }
        if delay is not None:
            params['sleep_seconds'] = delay
            
        result = self._rpc('send_batch', params)
        return result

    def read(self, queue_name: str, timeout: int, count: int) -> List[Job]:
        data = self._rpc('read', {
            'queue_name': queue_name,
            'sleep_seconds': timeout,
            'n': count
        })
        
        return [Job.from_response(job, queue=queue_name) for job in data]

    def pop(self, queue_name: str) -> Job | None:
        data = self._rpc('pop', {
            'queue_name': queue_name
        })
        
        return Job.from_response(data[0], queue=queue_name, popped=True) if data else None

    def archive(self, queue_name: str, job_or_id: int | Job) -> bool:
        msg_id = job_or_id.id if isinstance(job_or_id, Job) else job_or_id
        data = self._rpc('archive', {
            'queue_name': queue_name,
            'message_id': msg_id
        })
        
        return bool(data)

    def delete(self, queue_name: str, job_or_id: int | Job) -> bool:
        msg_id = job_or_id.id if isinstance(job_or_id, Job) else job_or_id
        data = self._rpc('delete', {
            'queue_name': queue_name,
            'message_id': msg_id
        })
        
        return bool(data)
