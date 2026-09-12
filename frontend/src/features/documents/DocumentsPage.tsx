import { FileStack } from "lucide-react";
import { useEffect } from "react";

import { useGetMeQuery } from "../../api/authApi";
import { useAppDispatch } from "../../app/hooks";
import { AppLayout } from "../../components/AppLayout";
import { PageHeader } from "../../components/PageHeader";
import { userSet } from "../auth/authSlice";
import { DocumentsList } from "./DocumentsList";
import { UploadZone } from "./UploadZone";

export function DocumentsPage() {
  const dispatch = useAppDispatch();
  const { data: me } = useGetMeQuery();

  useEffect(() => {
    if (me) dispatch(userSet(me));
  }, [me, dispatch]);

  return (
    <AppLayout>
      <PageHeader
        icon={FileStack}
        title="Documents"
        description="Upload, search, and inspect what's been indexed."
      />
      <UploadZone />
      <DocumentsList />
    </AppLayout>
  );
}
