"use client"

import { FormEvent , useState } from "react"
import { Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation";
import { getAuth, signInWithEmailAndPassword ,sendPasswordResetEmail} from "firebase/auth";

import { app } from "../../firebase";


export default function LoginForm(event: FormEvent) {
  const [showPassword, setShowPassword] = useState(false)

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const router = useRouter();
  const { toast } = useToast()

  const handleForgotPassword = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    sendPasswordResetEmail(getAuth(app), forgotPasswordEmail)
      .then(() => {
        console.log("success")
        toast({
          title: "Success",
          description: "Password reset email sent. Please check your inbox.",
          variant: "default",
        })
        setIsDialogOpen(false)
      })
      .catch((error) => {
        const errorMessage = error.message
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        })
      })
      .finally(() => {
        setForgotPasswordEmail("")
      })
  }


  

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");

    try {
      const credential = await signInWithEmailAndPassword(
        getAuth(app),
        email,
        password
      );
      const idToken = await credential.user.getIdToken();

      await fetch("/api/login", {
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });

      router.push("/");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">上德/奕德 內部登入系統</CardTitle>
          <CardDescription className="text-center">輸入信箱與密碼登入</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">信箱</Label>
              <Input id="email" type="email" placeholder="******@estate.tw" onChange={(e) => setEmail(e.target.value)} value={email}  required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">密碼</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  onChange={(e) => setPassword(e.target.value)}
                  value={password}
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-500" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-500" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full">登入</Button>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                
              </div>
            </div>
            
            <div className="text-sm text-center text-muted-foreground">
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="link" className="p-0 h-auto font-normal">忘記密碼?</Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>忘記密碼</DialogTitle>
                    <DialogDescription>
                      輸入信箱地址，將會寄送重設郵件給您
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleForgotPassword}>
                  <Label htmlFor="forgot-password-email" className="text-right">
                          電子信箱地址
                        </Label>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        
                        <Input
                          id="forgot-password-email"
                          type="email"
                          className="col-span-3"
                          value={forgotPasswordEmail}
                          onChange={(e) => setForgotPasswordEmail(e.target.value)}
                          required
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="submit">寄送重設郵件</Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </CardFooter>
          </form>
      </Card>
    </div>
  )
}