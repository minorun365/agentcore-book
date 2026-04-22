import { defineBackend } from "@aws-amplify/backend";
import { auth } from "./auth/resource";

// AmplifyのバックエンドにCognito認証のみを設定
defineBackend({
  auth,
});
