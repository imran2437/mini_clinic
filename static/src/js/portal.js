
$(document).ready(function () {
    $('#doctor_id').change(function () {
        var doctor_id = $(this).val();
        if (doctor_id) {
            $.ajax({
                url: '/get_slots',
                method: 'GET',
                data: { doctor_id: doctor_id },  // Send doctor ID as a parameter
                success: function (data) {
                    console.log('Slots:', data);  // Log the response for debugging
                    $('#slot_id').html(data);  // Insert the HTML directly into the slot container
                },
                error: function (xhr, status, error) {
                    console.error("Error fetching slots: ", error);
                }
            });
        } else {
            $('#slot_id').html('<p>Select a doctor to see available slots</p>');
        }
    });
});