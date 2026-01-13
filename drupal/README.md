# SageCompass – Drupal integration

Drupal 11 project for LangChain integration demo.

## Requirements:
- running local LangGraph instance
- LangSmith API key

## How to start:

  ```bash
  # Installing Drupal
  ddev start
  # If you haven't done it yet:
  ddev drush site:install --existing-config -y
  # To get the login url
  ddev drush uli

  # Make sure that LangGraph is running on http://0.0.0.0:2024
  cd ./../langgraph/backend && uv run langgraph dev --host 0.0.0.0
  ```

## How it works:

`vector_sync` module provides:

- https://sagecompass.ddev.site/admin/config/vector_sync/settings – To configure LangGraph Studio endpoint and API key
- https://sagecompass.ddev.site/admin/config/sagecompass/import – To bulk import documents into Drupal, it will automatically create tags and agent taxonomy terms
- https://sagecompass.ddev.site/admin/config/vector_sync/send – To batch send documents to LangGraph

If you want to test the integration quickly, upload documents via the import page. See ./../docs/assets/data.json for an example.

## Known errors:

### Docker - LangStudio network issue
On Local, Drupal is running inside a ddev initiated docker container, and it cannot connect to
LangGraph Studio, unless the Studio is started via `uv run langgraph dev --host 0.0.0.0`.

This enables LangSmith endpoint config like this `http://host.docker.internal:2024`, BUT! it disables
the default LangSmith because it doesn't see the http://0.0.0.0:2024 path.

The issue can be mitigated if you replace the 0.0.0.0 address manually to 127.0.0.1.
`https://eu.smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`
