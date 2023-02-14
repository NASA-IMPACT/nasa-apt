module.exports = {
  apiUrl: "http://api:80/v2",
  auth: {
    // DOCS: https://docs.amplify.aws/lib/auth/start/q/platform/js#re-use-existing-authentication-resource
    // Amazon Cognito Region
    region: "us-east-1",
    // Amazon Cognito User Pool ID. Needs to be set to the value from `make cognito-config`
    userPoolId: "us-east-1_xxx",
    // Amazon Cognito Web Client ID (26-char alphanumeric string). Needs to be set to the value from `make cognito-config`
    userPoolWebClientId: "xxx",
    // Manually set the authentication flow type. Default is 'USER_SRP_AUTH'
    authenticationFlowType: "USER_PASSWORD_AUTH",
    endpoint: "http://localstack:4566",
  },
  hostedAuthUi: "http://localstack:4566",
};
