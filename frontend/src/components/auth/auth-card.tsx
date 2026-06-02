import { Lock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface AuthCardProps {
  children: React.ReactNode;
  title: string;
  description?: string;
}

export function AuthCard({ children, title, description }: AuthCardProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
              <Lock className="h-6 w-6 text-white" />
            </div>
            <span className="font-bold text-2xl">PremiumServices</span>
          </div>
        </div>

        <Card className="shadow-xl border-0">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-2xl">{title}</CardTitle>
            {description && (
              <CardDescription>{description}</CardDescription>
            )}
          </CardHeader>
          <CardContent className="pt-6">{children}</CardContent>
        </Card>

        <p className="text-center text-sm text-muted-foreground mt-6">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}