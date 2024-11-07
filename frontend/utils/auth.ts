import { getTokens } from "next-firebase-auth-edge";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { clientConfig, serverConfig } from "../config";
// utils/auth.ts
export async function getAuthTokens() {
    const cookieStore = await cookies();
    const tokens = await getTokens(cookieStore, {
      apiKey: clientConfig.apiKey,
      cookieName: serverConfig.cookieName,
      cookieSignatureKeys: serverConfig.cookieSignatureKeys,
      serviceAccount: serverConfig.serviceAccount,
    });
  
    if (!tokens) {
      redirect('/login');
    }
  
    return tokens;
  }