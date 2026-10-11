import { useQuery } from "@tanstack/react-query";
import { getGraphExport, getNodeDetail } from "../services/api";

export function useGraph() {
  return useQuery({
    queryKey: ["graph", "export"],
    queryFn: getGraphExport,
  });
}

export function useNodeDetail(tag: string | null) {
  return useQuery({
    queryKey: ["graph", "node", tag],
    queryFn: () => getNodeDetail(tag as string),
    enabled: !!tag,
  });
}
