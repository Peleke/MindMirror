# MindMirror Shared

Shared components for MindMirror services including authentication, data models, and HTTP clients.

## Installation

This package is built and installed as part of the service deployment process.

## Usage

```python
from shared.auth import CurrentUser, get_current_user
from shared.clients import JournalServiceClient, create_journal_client
from shared.data_models import UserRole
``` 