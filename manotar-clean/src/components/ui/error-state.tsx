import { AlertCircle } from "lucide-react";

export const ErrorState = ({ message = "Something went wrong" }: { message?: string }) => (
  <div className="flex flex-col items-center justify-center w-full h-full min-h-[200px] text-destructive">
    <AlertCircle className="h-8 w-8 mb-2" />
    <p className="text-sm">{message}</p>
  </div>
); 