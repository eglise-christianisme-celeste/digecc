// Jenkins pipeline of DIGECC: the ecc-devops library, light profile (ci/ecc.json).
def revision = params.DEVOPS_REVISION ?: ''
if (!(revision ==~ /[a-f0-9]{40}/)) {
    error('DEVOPS_REVISION doit désigner un commit publié et revu de ecc-devops.')
}
// libraryPath belongs to the retriever: the library step itself ignores it.
library identifier: "ecc-devops@${revision}", retriever: modernSCM(
    scm: [
        $class: 'GitSCMSource',
        remote: 'https://github.com/eglise-christianisme-celeste/ecc-devops.git',
        credentialsId: 'ecc-github-read'
    ],
    libraryPath: 'shared-library/'
)
// Secrets, ruff, Django checks and tests under coverage, Sonar Quality Gate, image, Trivy, SBOM; RELEASE adds one
// approval, the Vault Transit signature and the GHCR publication.
eccPipeline(agent: 'seme-isolated', profile: 'light', release: params.RELEASE == true, ticket: params.TICKET ?: '',
            infrastructureRevision: params.INFRA_REVISION ?: '')
