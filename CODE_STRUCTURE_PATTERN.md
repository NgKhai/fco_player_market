# Code Structure Pattern

## Applied Laravel pattern

```text
Route -> FormRequest -> Controller -> Action -> SQLite query
```

## Current structure

```text
backend/app/
├── Actions/Players/
│   ├── GetPlayerDetailAction.php
│   ├── ListSeasonsAction.php
│   └── SearchPlayersAction.php
├── Http/
│   ├── Controllers/Api/PlayerController.php
│   └── Requests/Api/
│       ├── PlayerDetailRequest.php
│       └── PlayerSearchRequest.php
└── Models/
```

## Rules

- Controllers receive validated input, call one Action, and format the HTTP response.
- Actions own use-case logic and database queries; they do not depend on HTTP `Request` objects.
- FormRequests own validation and authorization at the HTTP seam.
- Query Builder is used directly because this project has one SQLite source; no Repository layer yet.
- Add DTOs only when a use case is called by HTTP, CLI, and queue with a non-trivial data shape.
- Add adapters, strategies, events, or jobs only when a real integration or background workflow exists.
