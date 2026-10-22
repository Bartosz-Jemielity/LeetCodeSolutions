// 3863. Minimum Operations to Sort a String
// https://leetcode.com/problems/minimum-operations-to-sort-a-string/
//
// Difficulty: Medium
// Language:   Java
// Runtime:    25 ms (beats 80.30%)
// Memory:     47.1 MB (beats 98.48%)
// Submitted:  2026-10-21
// Submission: https://leetcode.com/submissions/detail/2177758908/
//
// ------------------------------------------------------------
//
// You are given a string s consisting of lowercase English letters.
//
// In one operation, you can select any substring of s that is not the entire string and sort it in
// non-descending alphabetical order.
//
// Return the minimum number of operations required to make s sorted in non-descending order. If it is
// not possible, return -1.
//
// Example 1:
//
// Input: s = "dog"
//
// Output: 1
//
// Explanation:​​​​​​​
//
// - Sort substring "og" to "go".
// - Now, s = "dgo", which is sorted in ascending order. Thus, the answer is 1.
//
// Example 2:
//
// Input: s = "card"
//
// Output: 2
//
// Explanation:
//
// - Sort substring "car" to "acr", so s = "acrd".
// - Sort substring "rd" to "dr", making s = "acdr", which is sorted in ascending order. Thus, the
//   answer is 2.
//
// Example 3:
//
// Input: s = "gf"
//
// Output: -1
//
// Explanation:
//
// - It is impossible to sort s under the given constraints. Thus, the answer is -1.
//
// Constraints:
//
// - 1 <= s.length <= 10^5
// - s consists of only lowercase English letters.

class Solution {
    public int minOperations(String s) {
        int smallestC ='z'+1;
        int largestC = 'a'-1;
        boolean Notsorted = false;
        int n=s.length();
        for(int i=0;i<n;i++){
            if((int) s.charAt(i)<=smallestC){
                smallestC=s.charAt(i);
            }
            
            if((int) s.charAt(i)>=largestC){
                largestC=s.charAt(i);
            }
            else{
                Notsorted=true;
            }
        }

        if(!Notsorted){
            return 0;
        }
        else{
            if(s.length()==2){
                return -1;
            }
        }
       

        if(s.charAt(0)==smallestC || s.charAt(n-1)==largestC){
            return 1;
        }

                for (int i = 1; i < n - 1; i++) {
            if (s.charAt(i) == smallestC || s.charAt(i) == largestC) {
                return 2;
            }
        }

        return 3;
        
    }
}
