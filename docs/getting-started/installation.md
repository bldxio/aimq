# Installation

AIMQ can be installed and used in several ways depending on your needs:

## Command Line Tool (Recommended)

The easiest way to use AIMQ as a command line tool is to install it with `pipx`:

```bash
pipx install aimq
```

AIMQ can be installed using pip or poetry. We recommend using poetry for development.

## Using Poetry (Recommended)

```bash
poetry add aimq
```

Or clone the repository and install in development mode:

```bash
git clone https://github.com/bldxio/aimq.git
cd aimq
poetry install
```

## Using pip

```bash
pip install aimq
```

## Dependencies

AIMQ requires Python 3.11 or later and has the following main dependencies:

- easyocr: For OCR capabilities
- supabase: For queue and storage management
- langchain: For AI model integration
- pydantic: For data validation and settings management

These dependencies will be automatically installed when you install AIMQ.

## Configuration

After installation, you'll need to configure your Supabase credentials. Create a `.env` file in your project root:

```bash
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-api-key
```

Or set them as environment variables:

```bash
export SUPABASE_URL=your-project-url
export SUPABASE_KEY=your-api-key
```

## Verifying Installation

You can verify your installation by running:

```bash
poetry run aimq --version
```

This should display the version number of your AIMQ installation.
