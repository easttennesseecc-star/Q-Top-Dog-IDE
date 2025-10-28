import { ReactNode, CSSProperties } from "react";

interface FadeSlideProps {
  show: boolean;
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
}

export function FadeSlide({ show, children, className = "", style = {} }: FadeSlideProps) {
  return (
    <div
      className={
        `transition-all duration-500 ease-in-out transform ` +
        (show ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-4 pointer-events-none") +
        " " + className
      }
      style={{ ...style, willChange: "opacity, transform" }}
    >
      {children}
    </div>
  );
}
