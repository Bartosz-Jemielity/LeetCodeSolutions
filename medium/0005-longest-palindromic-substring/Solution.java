// 5. Longest Palindromic Substring
// https://leetcode.com/problems/longest-palindromic-substring/
//
// Difficulty: Medium
// Language:   Java
// Runtime:    27 ms (beats 29.68%)
// Memory:     44.8 MB (beats 44.65%)
// Submitted:  2026-10-27
// Submission: https://leetcode.com/submissions/detail/2183102054/
//
// ------------------------------------------------------------
//
// Given a string s, return the longest palindromic substring in s.
//
// Example 1:
//
// Input: s = "babad"
// Output: "bab"
// Explanation: "aba" is also a valid answer.
//
// Example 2:
//
// Input: s = "cbbd"
// Output: "bb"
//
// Constraints:
//
// - 1 <= s.length <= 1000
// - s consist of only digits and English letters.

class Solution {
    long h[];
    long pw[];
    long rev[];
    long p = 997;
    long mod = 100000009;
    int n;

    public long getHash(int l, int r) {
    long res = h[r] - (l > 0 ? (h[l - 1] * pw[r - l + 1]) % mod : 0);
    return (res % mod + mod) % mod;
}

public long getHashRv(int l, int r) {
    long res = rev[n - 1 - l] - (r < n - 1 ? (rev[n - r - 2] * pw[r - l + 1]) % mod : 0);
    return (res % mod + mod) % mod;
}

    boolean checkPali(int c, int k, boolean even) {
        int leftEnd = even ? c : c - 1;
        return getHash(leftEnd - k + 1, leftEnd) == getHashRv(c + 1, c + k);
    }

    public String longestPalindrome(String s) {
        n = s.length();
        h = new long[n];
        rev = new long[n];
        pw = new long[n];

        h[0] = s.charAt(0);
        pw[0] = 1;
        rev[0] = s.charAt(n - 1);
        for (int i = 1; i < n; i++) {
            h[i] = ((h[i - 1] * p) % mod + s.charAt(i)) % mod;
            pw[i] = (pw[i - 1] * p) % mod;
            rev[i] = ((rev[i - 1] * p) % mod + s.charAt(n - 1 - i)) % mod;
        }

        int bestStart = -1;
        int bestLen = 0;

        for (int i = 0; i < n; i++) {
            int maxLen = Math.min(i, n - i - 1);
            int minLen = 0;

            while (minLen < maxLen) {
                int mid = (maxLen + minLen + 1) / 2;
                //System.out.print("MID");
                //System.out.println(mid);
                if (checkPali(i, mid, false)) {
                    minLen = mid;
                } else {
                    maxLen = mid - 1;
                }
            }

            if (2 * minLen + 1 > bestLen) {
                bestLen = 2 * minLen + 1;
                bestStart = i - minLen;
            }

            maxLen = Math.min(i+1, n - i - 1);
            minLen = 0;

            while (minLen < maxLen) {
                int mid = (maxLen + minLen + 1) / 2;
                //System.out.print("MID");
                //System.out.println(mid);
                if (checkPali(i, mid, true)) {
                    minLen = mid;
                } else {
                    maxLen = mid - 1;
                }
            }

            if (2 * minLen> bestLen) {
                bestLen = 2 * minLen;
                bestStart = i - minLen + 1;
            }

        }
        return s.substring(bestStart, bestStart + bestLen);

    }
}
