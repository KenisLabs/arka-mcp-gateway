import { useToast } from "@/hooks/useToast";
import { CheckCircle, XCircle, Info, AlertTriangle, X } from "lucide-react";

const icons = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
  warning: AlertTriangle,
};

const styles = {
  success:
    "border-green-500 bg-green-50 dark:bg-green-950/20 text-gray-900 dark:text-gray-900",
  error:
    "border-red-500 bg-red-50 dark:bg-red-950/20 text-gray-900 dark:text-gray-900",
  info: "border-blue-500 bg-blue-50 dark:bg-blue-950/20 text-gray-900 dark:text-gray-900",
  warning:
    "border-yellow-500 bg-yellow-50 dark:bg-yellow-950/20 text-gray-900 dark:text-gray-900",
};

const iconStyles = {
  success: "text-green-600 dark:text-green-400",
  error: "text-red-600 dark:text-red-400",
  info: "text-blue-600 dark:text-blue-400",
  warning: "text-yellow-600 dark:text-yellow-400",
};

export function Toaster() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-full max-w-md">
      {toasts.map((toast) => {
        const Icon = icons[toast.type];
        return (
          <div
            key={toast.id}
            className={`rounded-lg border p-4 shadow-lg animate-in slide-in-from-bottom-5 ${
              styles[toast.type]
            }`}
          >
            <div className="flex items-start gap-3">
              <Icon
                className={`size-5 mt-0.5 flex-shrink-0 ${
                  iconStyles[toast.type]
                }`}
              />
              <p className="text-sm font-medium flex-1">{toast.message}</p>
              <button
                onClick={() => removeToast(toast.id)}
                className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity text-gray-900"
              >
                <X className="size-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
