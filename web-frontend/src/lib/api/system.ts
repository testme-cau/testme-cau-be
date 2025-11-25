import apiClient from '@/lib/api/client';
import type {
    BetaStatusResponse,
    WaitlistJoinPayload,
    WaitlistJoinResponse,
} from '@/types/api';

/**
 * Fetch current beta / closed-beta configuration from backend.
 */
export async function fetchBetaStatus(): Promise<BetaStatusResponse> {
    const { data } = await apiClient.get<BetaStatusResponse>(
        '/api/admin/config/status'
    );
    return data;
}

/**
 * Request access to the waitlist (closed beta).
 */
export async function requestWaitlistAccess(
    payload: WaitlistJoinPayload
): Promise<WaitlistJoinResponse> {
    const { data } = await apiClient.post<WaitlistJoinResponse>(
        '/api/waitlist',
        payload
    );
    return data;
}

