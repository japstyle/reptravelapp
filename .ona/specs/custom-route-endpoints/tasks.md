# Implementation Plan

- [ ] 1. Enhance station data API endpoint
  - Modify `/api/network-stations` endpoint to return structured station data with id, name_en, and name_ja fields
  - Extract Japanese names from network.json station data
  - Return JSON format: `{"stations": [{"id": "shibuya", "name_en": "Shibuya", "name_ja": "渋谷"}, ...]}`
  - Write unit tests to verify the endpoint returns correct data structure
  - _Requirements: 1.3, 5.3, 7.5_

- [ ] 2. Add input validation to route comparison endpoint
  - Add validation in `/route-compare` endpoint to check for missing origin or destination
  - Add validation to ensure origin and destination are different stations
  - Normalize station names using `route_finder._normalize_station` before processing
  - Use `route_finder._find_station` to validate stations exist in network
  - Return appropriate error messages in template context when validation fails
  - Write unit tests for each validation case (missing origin, missing destination, same station, invalid station)
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 3. Implement client-side autocomplete component
  - [ ] 3.1 Create autocomplete HTML structure and styling
    - Add hidden autocomplete dropdown container in route_compare.html
    - Style dropdown with CSS (positioning, colors, hover states, scrolling)
    - Add CSS for selected item highlighting
    - Ensure responsive design for mobile devices
    - _Requirements: 5.1, 5.2_
  
  - [ ] 3.2 Implement autocomplete JavaScript logic
    - Write function to load station data on page load
    - Implement `filterStations(query, stations)` function for case-insensitive matching on both English and Japanese names
    - Implement `showAutocomplete(matches, inputElement)` to display filtered results
    - Implement `hideAutocomplete()` to close dropdown
    - Implement `selectStation(station, inputElement)` to populate input with selected station
    - Add event listeners for input events (keyup, focus, blur)
    - Write integration tests to verify autocomplete filtering works correctly
    - _Requirements: 1.2, 1.3, 5.3_
  
  - [ ] 3.3 Add keyboard navigation support
    - Implement arrow key navigation (up/down) through autocomplete results
    - Implement Enter key to select highlighted item
    - Implement Escape key to close dropdown
    - Add visual highlighting for keyboard-selected items
    - Write tests for keyboard navigation functionality
    - _Requirements: 5.2_

- [ ] 4. Enhance error handling and user feedback
  - Add error message display area in route_compare.html template
  - Pass validation errors from backend to template context
  - Display user-friendly error messages for each error type (missing input, invalid station, same origin/destination, no routes found)
  - Style error messages with appropriate colors and icons
  - Write tests to verify error messages display correctly for each error case
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5. Add ARIA attributes for accessibility
  - Add `role="combobox"` to input fields
  - Add `aria-autocomplete="list"` to input fields
  - Add `role="listbox"` to autocomplete dropdown
  - Add `role="option"` to each autocomplete item
  - Add `aria-expanded` attribute that toggles based on dropdown state
  - Add `aria-activedescendant` to track keyboard-selected item
  - Test with screen reader to verify accessibility
  - _Requirements: 5.5_

- [ ] 6. Preserve user input on form submission
  - Ensure origin and destination values are preserved in input fields after form submission
  - Verify URL parameters are correctly populated when form is submitted
  - Test that users can modify their search without losing context
  - _Requirements: 5.4_

- [ ] 7. Add loading state and UX improvements
  - Add loading indicator when form is submitted
  - Disable submit button during route calculation to prevent double submission
  - Add smooth transitions for autocomplete dropdown appearance
  - Test that loading states work correctly
  - _Requirements: 5.2_

- [ ] 8. Write end-to-end integration tests
  - Write test for complete flow: page load → station selection → form submit → route display
  - Test with valid station pairs (e.g., Shibuya to Tokorozawa)
  - Test with invalid inputs to verify error handling
  - Test that routes are correctly scored and sorted
  - Verify that all route segments display correctly
  - _Requirements: 1.1, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 9. Add client-side form validation
  - Add JavaScript validation to check both fields are filled before submission
  - Display inline validation messages if fields are empty
  - Prevent form submission if validation fails
  - Write tests for client-side validation
  - _Requirements: 4.1, 4.2_

- [ ] 10. Optimize autocomplete performance
  - Add debouncing to autocomplete filtering if needed (delay filtering until user stops typing)
  - Limit number of displayed results to 10 items for better performance
  - Test autocomplete performance with full station dataset
  - _Requirements: 5.2_
