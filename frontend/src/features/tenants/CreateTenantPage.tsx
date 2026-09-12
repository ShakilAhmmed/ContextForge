import { zodResolver } from "@hookform/resolvers/zod";
import { Building2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

import { reportError } from "../../api/errors";
import { useCreateTenantMutation } from "../../api/tenantApi";
import { FormCard } from "../../components/FormCard";
import { FormField } from "../../components/FormField";
import { SubmitButton } from "../../components/SubmitButton";
import { type CreateTenantFormValues, createTenantSchema } from "./schema";

export function CreateTenantPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateTenantFormValues>({ resolver: zodResolver(createTenantSchema) });
  const [createTenant, { isLoading }] = useCreateTenantMutation();
  const navigate = useNavigate();

  async function onSubmit(values: CreateTenantFormValues) {
    try {
      const tenant = await createTenant(values).unwrap();
      navigate(`/register?tenant_id=${tenant.id}`);
    } catch (err) {
      reportError(err);
    }
  }

  return (
    <FormCard
      title="Create a tenant"
      icon={Building2}
      description="New here? Create your organization's tenant first, then register a user under it."
      footer={
        <>
          Already have a tenant?{" "}
          <Link to="/login" className="font-medium text-slate-900 underline">
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormField label="Organization name" {...register("name")} error={errors.name} />
        <FormField
          label="Slug (lowercase, numbers, hyphens)"
          {...register("slug")}
          error={errors.slug}
        />
        <SubmitButton loading={isLoading} className="w-full">
          Create tenant
        </SubmitButton>
      </form>
    </FormCard>
  );
}
