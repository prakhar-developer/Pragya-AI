import { useQuery } from "@tanstack/react-query";
import { getBenchmarks } from "../services/api";

export function useBenchmarks() {
  return useQuery({
    queryKey: ["benchmarks"],
    queryFn: getBenchmarks,
  });
}
