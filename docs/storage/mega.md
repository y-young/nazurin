# MEGA

<https://mega.io/>

## Configuration

!!! warning "Notice"

    Since authentication tokens are cached in database, after switching MEGA account, you'll need to delete `mega` document in `nazurin` collection from the database.

### STORAGE

Append `Mega`. For more information, see [Configuration](../getting-started/configuration.md/#storage).

### MEGA_USER

:material-exclamation-thick: Required

Login email.

### MEGA_PASS

:material-exclamation-thick: Required

Login password.

## Encoding Issue

Due to unknown reasons, there're encoding issues with special filenames (e.g.: special or full-width characters) on MEGA.
These filenames may be wrongly displayed on MEGA Android & iOS clients, and cannot be synced through MEGASync. However, MEGA Web client can handle these files correctly, so to solve this problem, do the following:

1.  Create a temporary directory and set `STORAGE_DIR` to it
2.  Periodically log into MEGA **Web** client
3.  **Copy** all files from temporary directory to archive directory (Do not use _move_)
4.  Delete files in temporary directory
5.  Problem solved

!!! tip

    Of course you can modify filename format to avoid this problem.
