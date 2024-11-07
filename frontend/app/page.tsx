import { redirect } from "next/navigation";
import { getAuthTokens } from "@/utils/auth";
import HomePage from "./HomePage";

export default async function Home() {
  const tokens = await getAuthTokens();
  

  if (!tokens) {
    redirect('/login');
  }

  return <HomePage email={ tokens.decodedToken.email} />;
}

