
stages:
  - build
  - release

trigger_digitalai_release:
  stage: release
  image: alpine:3.22

  needs:
    - job: build
      artifacts: false

  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_COMMIT_TAG'

  before_script:
    - apk add --no-cache curl jq

  script:
    - |
      set -eu

      : "${DIGITALAI_URL:?Missing DIGITALAI_URL}"
      : "${DIGITALAI_PAT:?Missing DIGITALAI_PAT}"
      : "${DIGITALAI_TEMPLATE_ID:?Missing DIGITALAI_TEMPLATE_ID}"

      # Ensure config.json exists and contains a JSON object.
      test -f config.json || {
        echo "ERROR: config.json not found in repository"
        exit 1
      }

      jq -e 'type == "object"' config.json > /dev/null

      # Build the request body without losing JSON data types.
      jq -n \
        --arg title "GitLab ${CI_PROJECT_PATH} pipeline ${CI_PIPELINE_ID}" \
        --slurpfile config config.json \
        '{
          releaseTitle: $title,
          variables: $config[0]
        }' > request.json

      # Start the release and save the API response.
      URL="${DIGITALAI_URL%/}/api/v1/templates/${DIGITALAI_TEMPLATE_ID}/start"

      curl --fail-with-body --silent --show-error \
        --request POST \
        --header "x-release-personal-token: ${DIGITALAI_PAT}" \
        --header "Content-Type: application/json" \
        --header "Accept: application/json" \
        --data-binary @request.json \
        --output response.json \
        --write-out "HTTP status: %{http_code}\n" \
        "$URL"

      echo "Digital.ai release started. API response:"
      jq '{id, title, status}' response.json
