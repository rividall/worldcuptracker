import { apiGet } from "@/api/client";
import type {
  Bracket,
  CupNumbers,
  Group,
  LastSync,
  TeamDetail,
  TeamListItem,
} from "@/api/types";

export function getGroups(): Promise<Group[]> {
  return apiGet<Group[]>("/groups");
}

export function getBracket(): Promise<Bracket> {
  return apiGet<Bracket>("/bracket");
}

export function getLastSync(): Promise<LastSync> {
  return apiGet<LastSync>("/meta/last-sync");
}

export function getTeams(): Promise<TeamListItem[]> {
  return apiGet<TeamListItem[]>("/teams");
}

export function getTeam(teamId: number): Promise<TeamDetail> {
  return apiGet<TeamDetail>(`/teams/${teamId}`);
}

export function getCupNumbers(): Promise<CupNumbers> {
  return apiGet<CupNumbers>("/stats");
}
