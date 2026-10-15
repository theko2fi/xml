
stages:
  - build
  - release

# Your existing build job must be named "build".
# It must finish successfully before the release job runs.

trigger_digitalai_release:
  stage: release
  image: curlimages/curl:latest

  needs:
    - job: build
      artifacts: false

  variables:
    GIT_STRATEGY: none

  script:
    - |
      set -eu

      : "${DIGITALAI_URL:?Missing DIGITALAI_URL}"
      : "${DIGITALAI_PAT:?Missing DIGITALAI_PAT}"
      : "${DIGITALAI_TEMPLATE_ID:?Missing DIGITALAI_TEMPLATE_ID}"

      RELEASE_URL="${DIGITALAI_URL%/}/api/v1/templates/${DIGITALAI_TEMPLATE_ID}/start"

      echo "Starting Digital.ai release for pipeline ${CI_PIPELINE_ID}"

      curl --fail-with-body --silent --show-error \
        --request POST \
        --header "x-release-personal-token: ${DIGITALAI_PAT}" \
        --header "Content-Type: application/json" \
        --header "Accept: application/json" \
        --data "{
          \"releaseTitle\": \"GitLab pipeline ${CI_PIPELINE_ID}\"
        }" \
        "${RELEASE_URL}"

      echo "Digital.ai Release API request completed successfully."
