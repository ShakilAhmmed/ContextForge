import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";

import { useRegisterMutation } from "../../api/authApi";
import { reportError } from "../../api/errors";
import { FormCard } from "../../components/FormCard";
import { FormField } from "../../components/FormField";
import { SubmitButton } from "../../components/SubmitButton";
import { type RegisterFormValues, registerSchema } from "./schema";

export function RegisterPage() {
  const [searchParams] = useSearchParams();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { tenant_id: searchParams.get("tenant_id") ?? "" },
  });
  const [registerUser, { isLoading }] = useRegisterMutation();
  const navigate = useNavigate();

  async function onSubmit(values: RegisterFormValues) {
    try {
      await registerUser(values).unwrap();
      toast.success("Registered, log in to continue");
      navigate("/login");
    } catch (err) {
      reportError(err);
    }
  }

  return (
    <FormCard
      title="Register"
      icon={UserPlus}
      footer={
        <>
          Already registered?{" "}
          <Link to="/login" className="font-medium text-slate-900 underline">
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormField label="Tenant ID" {...register("tenant_id")} error={errors.tenant_id} />
        <FormField label="Email" type="email" {...register("email")} error={errors.email} />
        <FormField
          label="Password"
          type="password"
          {...register("password")}
          error={errors.password}
        />
        <SubmitButton loading={isLoading} className="w-full">
          Register
        </SubmitButton>
      </form>
    </FormCard>
  );
}
