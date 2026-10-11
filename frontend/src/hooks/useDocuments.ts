import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useState } from "react";
import {
  getDocuments,
  uploadDocument,
  uploadDocuments,
} from "../services/api";

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}

export function useUploadDocuments() {
  const qc = useQueryClient();
  const [progress, setProgress] = useState(0);
  const mutation = useMutation({
    mutationFn: (files: File[]) => {
      setProgress(0);
      return uploadDocuments(files, setProgress);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
  return { ...mutation, progress };
}
