## Description

Simple service for user interaction with database and s3

## Usage

Set following variables in env or put the into .env file:
- LOCALSTACK_AUTH_TOKEN

These are required for cognito to send emails
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASS

For connection to some local db, override database URLs:
- DATABASE_URL_SYNC
- DATABASE_URL_ASYNC
- CELERY_RESULT_BACKEND (either override or set smth other than db)


### deployment
For deployment just run `make run`

### lde
For development with hot-reload run `make dev`


## Functionalities

### SignIn

```mermaid
sequenceDiagram
    actor u as user
    participant w as web
    participant db as database
    participant a as cognito
    
    u ->>+ w: /user/sign-in
    w ->> a: initiate auth
    a ->> w: access token
    w ->> u: set cookie with token
    w ->>- u: redirect to /dialog
```

### Registration

```mermaid
sequenceDiagram
    actor u as user
    participant w as web
    participant db as database
    participant c as celery
    participant a as cognito
    
    u ->>+ w: /user/sign-up
    w ->> db: save user+email
    w ->>- u: ok
    w ->> c: schedule task
    c ->> db: get user details
    c ->> a: sign-up
    a ->> u: send confirmation email
    
    u ->>+ w: /user/confirm
    w ->> a: confirm
    a ->> w: 
    w ->> u: ok
```

### Generation

```mermaid
sequenceDiagram
    actor u as user
    participant w as web
    participant db as database
    participant c as celery
    participant a as s3
    
    u ->> w: /dialog/ws/{token}
    w ->> u: 
    u ->>+ w: /dialog/ws/{token}: submit
    w ->> db: save message details
    w ->>+ c: schedule task
    c ->> a: store message
    c ->> db: update message status
    c ->> a: sign-up
    c ->>- w: return result
    w ->>- u: /dialog/ws/{token}: return output
```

