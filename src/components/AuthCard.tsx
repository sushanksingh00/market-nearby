import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { User, Store, Shield, Mail, Lock } from "lucide-react";

const AuthCard = () => {
  const [userType, setUserType] = useState<"customer" | "shopkeeper" | "admin">("customer");

  const getUserIcon = () => {
    switch (userType) {
      case "customer": return <User className="w-5 h-5" />;
      case "shopkeeper": return <Store className="w-5 h-5" />;
      case "admin": return <Shield className="w-5 h-5" />;
    }
  };

  const getUserTypeLabel = () => {
    switch (userType) {
      case "customer": return "Customer Login";
      case "shopkeeper": return "Shopkeeper Login";
      case "admin": return "Admin Login";
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-hero p-4">
      <Card className="w-full max-w-md shadow-glow">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-gradient-primary rounded-full text-white">
              {getUserIcon()}
            </div>
          </div>
          <CardTitle className="text-2xl">{getUserTypeLabel()}</CardTitle>
        </CardHeader>
        
        <CardContent>
          <Tabs value={userType} onValueChange={(value) => setUserType(value as any)} className="mb-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="customer" className="text-xs">
                <User className="w-4 h-4 mr-1" />
                Customer
              </TabsTrigger>
              <TabsTrigger value="shopkeeper" className="text-xs">
                <Store className="w-4 h-4 mr-1" />
                Shop
              </TabsTrigger>
              <TabsTrigger value="admin" className="text-xs">
                <Shield className="w-4 h-4 mr-1" />
                Admin
              </TabsTrigger>
            </TabsList>
          </Tabs>

          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Input 
                  id="email" 
                  type="email" 
                  placeholder="Enter your email"
                  className="pl-10"
                />
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input 
                  id="password" 
                  type="password" 
                  placeholder="Enter your password"
                  className="pl-10"
                />
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              </div>
            </div>

            <Button className="w-full" size="lg">
              Sign In
            </Button>
          </form>

          <div className="mt-6 space-y-3">
            <Button variant="outline" className="w-full">
              Create New Account
            </Button>
            <Button variant="ghost" className="w-full text-sm">
              Forgot Password?
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCard;