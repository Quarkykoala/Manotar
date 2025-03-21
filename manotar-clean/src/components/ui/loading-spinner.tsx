import { Loader2 } from "lucide-react";

export const LoadingSpinner = () => (
  <div className="flex items-center justify-center w-full h-full min-h-[200px]">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
); 