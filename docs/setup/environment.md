# Environment Variable Strategy

This document outlines the environment variable strategy for the Manobal project, detailing how environment variables are organized, used, and maintained across different components and environments.

## Environment File Structure

The project uses a standardized approach to environment variables:

- `.env.example` - Template files with placeholder values (committed to version control)
- `.env` - Local development environment variables (not committed)
- `.env.test` - Test environment variables (not committed)
- `.env.production` - Production environment variables (not committed)

These files exist at three levels:

1. **Root level**: Project-wide configuration accessible to all components
2. **Backend level**: Backend-specific configuration
3. **Frontend level**: Frontend-specific configuration

## Setup

To set up environment variables for a new environment:

1. Run the environment setup script:

   ```bash
   # For Windows (PowerShell)
   ./scripts/setup/setup_env.ps1 [environment]
   
   # For Linux/macOS
   ./scripts/setup/setup_env.sh [environment]
   ```
   
   Where `[environment]` is one of:
   - `development` (default)
   - `test`
   - `production`

2. Edit the generated `.env` files with your actual configuration values.

## Environment Variables by Component

### Root Level

Root-level environment variables contain configuration that may be needed by multiple components or scripts.

Key variables:
- Database connections
- API keys
- Deployment configuration
- Shared secrets

### Backend-specific

Backend environment variables include:
- Flask configuration
- Database connections
- Authentication secrets
- API rate limits
- Logging configuration

### Frontend-specific

Frontend environment variables include:
- API endpoints
- Feature flags
- UI configuration
- Analytics IDs

## Security Considerations

1. **Never commit actual environment files**: Only `.env.example` files should be committed
2. **Rotate secrets regularly**: API keys and JWT secrets should be rotated periodically
3. **Restrict access**: Production environment variables should be accessible only to authorized team members
4. **Use environment-specific values**: Different environments (dev, test, prod) should use different variable values, especially for secrets

## Adding New Environment Variables

When adding new environment variables:

1. Add the variable to the appropriate `.env.example` file with a placeholder value
2. Document the variable in this file and any relevant component documentation
3. Update the CI/CD pipeline if necessary to include the new variable
4. Inform team members to update their local environment files

## Environment Variable Naming Conventions

- Backend variables: Standard naming (e.g., `DATABASE_URL`)
- Frontend variables: Prefix with `NEXT_PUBLIC_` for client-side variables (e.g., `NEXT_PUBLIC_API_URL`)
- Boolean flags: Use `ENABLE_FEATURE` or `DISABLE_FEATURE` format
- Numeric values: Use clear units in the name (e.g., `MAX_REQUESTS_PER_MINUTE`)

## Environment-specific Overrides

Configuration that varies by environment:

1. **Development**: Local services, debug flags enabled
2. **Test**: Test databases, mock services
3. **Production**: Production services, no debug flags, strict security 

## Environment File Maintenance

The project includes scripts to help maintain and verify environment files:

```bash
# For Windows (PowerShell)
./scripts/deploy/env_cleanup.ps1

# For Linux/macOS
./scripts/deploy/env_cleanup.sh
```

These scripts perform the following checks:
1. Verify that all required `.env.example` files exist at all levels
2. Identify local environment files that should not be committed to Git
3. Provide guidance on ensuring these files are properly ignored by Git
4. Validate that all variables from `.env.example` files exist in the corresponding environment files

Run these scripts periodically, especially before committing changes, to ensure environment files are properly maintained and complete. 