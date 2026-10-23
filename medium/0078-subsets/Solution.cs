// 78. Subsets
// https://leetcode.com/problems/subsets/
//
// Difficulty: Medium
// Language:   C#
// Runtime:    0 ms (beats 100.00%)
// Memory:     45.8 MB (beats 96.20%)
// Submitted:  2026-10-22
// Submission: https://leetcode.com/submissions/detail/2178925838/
//
// ------------------------------------------------------------
//
// Given an integer array nums of unique elements, return all possible subsets (the power set).
//
// The solution set must not contain duplicate subsets. Return the solution in any order.
//
// Example 1:
//
// Input: nums = [1,2,3]
// Output: [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]
//
// Example 2:
//
// Input: nums = [0]
// Output: [[],[0]]
//
// Constraints:
//
// - 1 <= nums.length <= 10
// - -10 <= nums[i] <= 10
// - All the numbers of nums are unique.

public class Solution {
    public IList<IList<int>> Subsets(int[] nums) {
        List<IList<int>> anw = new  List<IList<int>>();
        anw.Add(new List<int>());

        foreach(var x in nums){
            List<IList<int>> toAdd = new  List<IList<int>>();
            foreach(var l in anw){
            List<int> temp = new(l);
            temp.Add(x);
            toAdd.Add(temp);
            }

            foreach(var toad in toAdd){
                anw.Add(toad);
            }
        }

        return anw;
    }
}
