# Datacom Kudos

An internal team recognition app where colleagues can celebrate great work with short public messages.

## Features

- Select a colleague and send a kudos message.
- View recent kudos in the shared dashboard feed.
- Toggle administrator mode to hide inappropriate kudos.
- Permanently delete kudos after confirmation.
- Persist prototype submissions and moderation state with `localStorage`.

## Run Locally

Open [Process_flow/index.html](Process_flow/index.html) in a browser. No build step or package installation is required.

## Project Files

- [Process_flow/index.html](Process_flow/index.html): Dashboard markup and form controls.
- [Process_flow/styles.css](Process_flow/styles.css): Responsive visual styling.
- [Process_flow/app.js](Process_flow/app.js): Feed rendering, submissions, and moderation behavior.
- [Process_flow/SPECIFICATION.md](Process_flow/SPECIFICATION.md): Requirements and data-model specification.

## Prototype Note

Administrator mode is simulated in the frontend for this prototype. A production implementation should authenticate users and enforce administrator permissions through a backend API and database.