#ifndef PERMUTATION_H
#define PERMUTATION_H
#include "array.h"
#include "arraysaccessor.h"

/* The Permutation class iterates through all permutations of a set of
 * objects.  In order to avoid equivalent permutations, equality must be
 * defined among the objects.
 */
template<typename Type>
class Permutation
{
public:
    Permutation()
        : hasNext_(false)
    { /* NOP */ }

    Permutation(const Array<Type>& vals) 
    { setValues(vals); }


    void setValues(const Array<Type>& vals) 
    {
        values_ = vals;

        perm_.clear();
        perm_.growToSize(values_.size());
        filled_.clear();
        filled_.growToSize(values_.size());

        // Keep track of duplicates.  We don't want to double-count
        // equivalent permutations.
        prevDuplicate_.clear();
        numLaterDuplicates_.clear();
        for (int i = 0; i < values_.size(); i++) {
            int prevDuplicate = -1;
            for (int j = 0; j < i; j++) {
                if (values_[j] == values_[i]) {
                    prevDuplicate = j;
                    numLaterDuplicates_[j]++;
                }
            }
            prevDuplicate_.append(prevDuplicate);
            numLaterDuplicates_.append(0);
        }

        reset();
    }

    void reset()
    {
        skips_.clear();
        skips_.growToSize(values_.size());

        // Return to first permutation
        for (int i = 0; i < skips_.size(); i++) { 
            skips_[i] = 0;
        }

        for (int i = 0; i < values_.size(); i++) {
            perm_[i] = values_[i];
        }

        // NOTE: this could be wrong if we have 0 values.  Boundary case.
        hasNext_ = true;
    }

    ~Permutation() { /* NOP */ }

    int size() {
        return values_.size();
    }

    bool hasNext() {
        return hasNext_;
    }

    // Advance to the next permutation.
    void next() {

        // Advance to next permutation
        hasNext_ = false;
        for (int i = size() - 2; i >= 0; i--) {
            skips_[i]++;
            int numSkips = skips_[i];
            // Add up all previous skips
            int prevIndex = i;
            while (prevDuplicate_[prevIndex] >= 0) {
                numSkips += skips_[prevDuplicate_[prevIndex]];
                prevIndex = prevDuplicate_[prevIndex];
            }
            if (numSkips < size() - i - numLaterDuplicates_[i]) {
                hasNext_ = true;
                break;
            } else {
                skips_[i] = 0;
            }
        }

        // Mark all slots as empty
        for (int i = 0; i < size(); i++) {
            filled_[i] = false;
        }

        for (int i = 0; i < size(); i++) {
            int numSkips = skips_[i];
            if (prevDuplicate_[i] >= 0) {
                numSkips += skips_[prevDuplicate_[i]];
            }
            int currIndex = 0;
            while (numSkips > 0 || filled_[currIndex]) {
                if (!filled_[currIndex]) {
                    numSkips--;
                }
                currIndex++;
                assert (currIndex < size()); 
            }
            perm_[currIndex] = values_[i];
            filled_[currIndex] = true;
        }
    }

    Type operator[](int idx) {
        return perm_[idx];
    }


private:
    bool hasNext_;
    Array<int> skips_;
    Array<Type> values_;
    Array<bool> filled_;
    Array<Type> perm_;
    Array<int> prevDuplicate_;
    Array<int> numLaterDuplicates_;
};
#endif // ndef PERMUTATION_H
