import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  change?: number;
  icon?: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatsCard({
  title,
  value,
  description,
  change,
  icon: Icon,
  trend,
}: StatsCardProps) {
  const getTrendIcon = () => {
    if (trend === 'up' || (change && change > 0)) {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    }
    if (trend === 'down' || (change && change < 0)) {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    }
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  };

  const getChangeColor = () => {
    if (trend === 'up' || (change && change > 0)) return 'text-green-500';
    if (trend === 'down' || (change && change < 0)) return 'text-red-500';
    return 'text-muted-foreground';
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {description && (
              <p className="text-xs text-muted-foreground">{description}</p>
            )}
          </div>
          {Icon && (
            <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center">
              <Icon className="h-6 w-6 text-muted-foreground" />
            </div>
          )}
        </div>

        {change !== undefined && (
          <div className="mt-4 flex items-center gap-1">
            {getTrendIcon()}
            <span className={cn('text-sm font-medium', getChangeColor())}>
              {change > 0 ? '+' : ''}
              {change}%
            </span>
            <span className="text-sm text-muted-foreground">from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}