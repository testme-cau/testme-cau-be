import apiClient from "./client";
import type {
  Group,
  GroupCreateRequest,
  GroupUpdateRequest,
  GroupResponse,
  GroupListResponse,
} from "@/types/api";

export const groupsApi = {
  /**
   * Create a new group
   */
  async createGroup(data: GroupCreateRequest): Promise<Group> {
    const response = await apiClient.post<GroupResponse>("/api/groups", data);
    return response.data.group;
  },

  /**
   * Get all groups for the current user
   */
  async getGroups(): Promise<Group[]> {
    const response = await apiClient.get<GroupListResponse>("/api/groups");
    return response.data.groups;
  },

  /**
   * Get a specific group by ID
   */
  async getGroup(groupId: string): Promise<Group> {
    const response = await apiClient.get<GroupResponse>(`/api/groups/${groupId}`);
    return response.data.group;
  },

  /**
   * Update a group
   */
  async updateGroup(groupId: string, data: GroupUpdateRequest): Promise<Group> {
    const response = await apiClient.put<GroupResponse>(`/api/groups/${groupId}`, data);
    return response.data.group;
  },

  /**
   * Delete a group
   */
  async deleteGroup(groupId: string): Promise<void> {
    await apiClient.delete(`/api/groups/${groupId}`);
  },
};

