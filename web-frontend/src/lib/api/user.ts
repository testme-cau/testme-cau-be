import apiClient from '@/lib/api/client';
import type {
    LanguageListResponse,
    LanguageOption,
    UserProfile,
    UserProfileResponse,
    UserProfileUpdateRequest,
} from '@/types/api';

const PROFILE_ENDPOINT = '/api/user/profile';
const LANGUAGES_ENDPOINT = '/api/user/languages';

export async function getUserProfile(): Promise<UserProfile> {
    const { data } = await apiClient.get<UserProfileResponse>(PROFILE_ENDPOINT);
    return data.user;
}

export async function updateUserProfile(
    payload: UserProfileUpdateRequest
): Promise<UserProfile> {
    const { data } = await apiClient.put<UserProfileResponse>(
        PROFILE_ENDPOINT,
        payload
    );
    return data.user;
}

export async function getSupportedLanguages(): Promise<LanguageOption[]> {
    const { data } =
        await apiClient.get<LanguageListResponse>(LANGUAGES_ENDPOINT);
    return data.languages;
}

