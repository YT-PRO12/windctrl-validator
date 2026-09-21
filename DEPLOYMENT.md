# Streamlit Community Cloud deployment

1. Publish this repository to your GitHub account as public.
2. Sign in to Streamlit Community Cloud and authorize access to the repository.
3. Select the repository, branch `main` and main file `streamlit_app.py`.
4. Under advanced settings use Python 3.12, then deploy.
5. Choose public app access and confirm it loads in a signed-out browser.

The root `requirements.txt` installs the local package, whose `pyproject.toml`
pins the primary runtime dependencies. No secrets or database are required.
`.streamlit/config.toml` sets the theme and upload limit.

## Verification before adding a resume link

Check the signed-out app URL, select or filter the sample data, change a
threshold and confirm charts and output update. Upload the provided sample CSV
and check malformed input displays a readable message. Inspect deployment logs
for startup failures. Verify the repository and its current commit are public.

Record the actual deployed URL only after these checks. A local server or
configuration file is not evidence of a public deployment. Community Cloud
apps can sleep when unused; recheck availability before sharing a resume.

Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
