import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  generateWorkOrderPDF,
  getConflicts,
  resolveConflict,
} from "../services/api";

export function useConflicts(status?: string) {
  return useQuery({
    queryKey: ["conflicts", status ?? "all"],
    queryFn: () => getConflicts(status),
  });
}

export function useResolveConflict() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => resolveConflict(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conflicts"] }),
  });
}

export function useGenerateWorkOrder() {
  return useMutation({
    mutationFn: (id: string) => generateWorkOrderPDF(id),
  });
}
