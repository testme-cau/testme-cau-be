import Link from "next/link";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg" | "xl";
  href?: string;
  showLink?: boolean;
}

const sizeClasses = {
  sm: "text-xl",
  md: "text-2xl",
  lg: "text-3xl",
  xl: "text-4xl",
};

export function Logo({ 
  className, 
  size = "md", 
  href = "/", 
  showLink = true 
}: LogoProps) {
  const logoContent = (
    <span className={cn("font-bold", sizeClasses[size], className)}>
      <span className="text-teal-600">test</span>
      <span className="text-gray-900">.me</span>
    </span>
  );

  if (showLink) {
    return (
      <Link 
        href={href} 
        className="inline-block transition-opacity hover:opacity-80"
      >
        {logoContent}
      </Link>
    );
  }

  return logoContent;
}

