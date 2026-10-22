// 19. Remove Nth Node From End of List
// https://leetcode.com/problems/remove-nth-node-from-end-of-list/
//
// Difficulty: Medium
// Language:   C#
// Runtime:    1 ms (beats 3.29%)
// Memory:     42.6 MB (beats 6.39%)
// Submitted:  2025-12-02
// Submission: https://leetcode.com/submissions/detail/1845350677/
//
// ------------------------------------------------------------
//
// Given the head of a linked list, remove the n^th node from the end of the list and return its head.
//
// Example 1:
//  [image: https://assets.leetcode.com/uploads/2020/10/03/remove_ex1.jpg]
//
// Input: head = [1,2,3,4,5], n = 2
// Output: [1,2,3,5]
//
// Example 2:
//
// Input: head = [1], n = 1
// Output: []
//
// Example 3:
//
// Input: head = [1,2], n = 1
// Output: [1]
//
// Constraints:
//
// - The number of nodes in the list is sz.
// - 1 <= sz <= 30
// - 0 <= Node.val <= 100
// - 1 <= n <= sz
//
// Follow up: Could you do this in one pass?

/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     public int val;
 *     public ListNode next;
 *     public ListNode(int val=0, ListNode next=null) {
 *         this.val = val;
 *         this.next = next;
 *     }
 * }
 */
public class Solution {

    public ListNode RemoveNthFromEnd(ListNode head, int n) {
    Stack<ListNode> s = new Stack<ListNode>();
        ListNode temphead = head;

        while(temphead!=null){
            s.Push(temphead);
            temphead = temphead.next;
        }
        Console.WriteLine(s.Count);
        if(s.Count==1){
            return null;
        }

        ListNode prev = null;
        for(int i=0;i<n;i++){
            prev = s.Pop();
        }

        ListNode last = null;
        if(s.Count>=1){
        last = s.Pop();
        }

        if(last==null){
            return head.next;
        }
        else{
        last.next=prev.next;
        prev.next=null;
        return head;
        }

    }
}
