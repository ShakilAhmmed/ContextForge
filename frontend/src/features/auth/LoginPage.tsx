import { zodResolver } from "@hookform/resolvers/zod";
import { LogIn } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

import { useLoginMutation } from "../../api/authApi";
import { reportError } from "../../api/errors";
import { FormCard } from "../../components/FormCard";
import { FormField } from "../../components/FormField";
import { SubmitButton } from "../../components/SubmitButton";
import { type LoginFormValues, loginSchema } from "./schema";

export function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });
  const [login, { isLoading }] = useLoginMutation();
  const navigate = useNavigate();

  async function onSubmit(values: LoginFormValues) {
    try {
      // Sets the httpOnly auth cookie + CSRF cookie as a side effect of the
      // response - nothing client-side to store, just go.
      await login(values).unwrap();
      navigate("/documents");
    } catch (err) {
      reportError(err);
    }
  }

  return (
    <FormCard
      title="Log in"
      icon={LogIn}
      footer={
        <>
          Need a tenant first?{" "}
          <Link to="/create-tenant" className="font-medium text-slate-900 underline">
            Create one
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormField label="Email" type="email" {...register("email")} error={errors.email} />
        <FormField
          label="Password"
          type="password"
          {...register("password")}
          error={errors.password}
        />
        <SubmitButton loading={isLoading} className="w-full">
          Log in
        </SubmitButton>
      </form>
    </FormCard>
  );
}
