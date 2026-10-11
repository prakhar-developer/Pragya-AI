import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  getExpertContributions,
  submitExpertContribution,
} from "../services/api";
import type { ExpertContributionInput } from "../services/types";

export function useExpertContributions() {
  return useQuery({
    queryKey: ["expert", "contributions"],
    queryFn: getExpertContributions,
  });
}

export function useSubmitContribution() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ExpertContributionInput) =>
      submitExpertContribution(payload),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["expert", "contributions"] }),
  });
}
