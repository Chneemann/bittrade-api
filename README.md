# BITTRADE API

## Env Configuration

To configure your backend application, you need to create an `.env` file in the config folder of your project. This file contains various environment-specific settings, including email, security, and monitoring configuration.

### Step 1: Create the `.env` file

Create a file named `.env` inside the config folder of your project:

```
/your-project-root/
└── config/
    ├── .env_example
    └── .env  ← create this file
```

You can also simply rename or copy the existing `.env_example` file:

```bash
cp config/.env_example config/.env
```

Then open `config/.env` and adjust the values according to your environment.

### Step 2: Add the required configuration

Open the `.env` file and include the following lines according to your needs:

```env
# General settings
DEBUG=False
SECRET_KEY=your_secret_key_here
```
