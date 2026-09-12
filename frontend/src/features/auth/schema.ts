import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  tenant_id: z.string().uuid("Enter a valid tenant ID"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "At least 8 characters"),
});

export type RegisterFormValues = z.infer<typeof registerSchema>;
