import { Card } from "@/components/ui/card";

interface TooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
}

export const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
  if (!active || !payload) return null;

  return (
    <Card className="bg-background/95 backdrop-blur-sm p-3 shadow-lg border-none animate-in zoom-in-50 duration-200">
      <p className="font-medium">{label}</p>
      <div className="space-y-1 mt-2">
        {payload.map((item: any, index: number) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-muted-foreground">
              {item.name}: {item.value}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}; 