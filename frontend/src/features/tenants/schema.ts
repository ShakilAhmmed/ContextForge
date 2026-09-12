import { z } from "zod";

export const createTenantSchema = z.object({
  name: z.string().min(1, "Organization name is required"),
  slug: z
    .string()
    .min(1, "Slug is required")
    .regex(/^[a-z0-9-]+$/, "Lowercase letters, numbers, and hyphens only"),
});

export type CreateTenantFormValues = z.infer<typeof createTenantSchema>;
