$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    function update_form_data(res) {
        $("#product_id").val(res.product_id);
        $("#customer_id").val(res.customer_id);
        $("#product_name").val(res.product_name);
        $("#recommendation_name").val(res.recommendation_name);
        $("#recommend_product_id").val(res.recommend_product_id);
        $("#recommend_type").val(res.recommend_type);
        $("#rec_success").val(res.rec_success);
    }

    function clear_form_data() {
        $("#product_id").val("");
        $("#customer_id").val("");
        $("#product_name").val("");
        $("#recommendation_name").val("");
        $("#recommend_product_id").val("");
        $("#recommend_type").val("Select");
        $("#rec_success").val("");
    }

    function flash_message(message, type = "info") {
        const alertClass = `alert-${type}`;
        const container = $("#flash_container");
    
        container
            .removeClass("alert-info alert-success alert-warning alert-danger")
            .addClass(alertClass)
            .fadeIn();
    
        $("#flash_message").html(message);
    
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            container.fadeOut("slow");
        }, 10000);
    }

    function listAllRecommendations() {
        let ajax = $.ajax({
            type: "GET",
            url: "/recommendations",
            contentType: "application/json",
        });

        ajax.done(function(res){
            $("#search_results tbody").empty();
            for (let rec of res) {
                let row = `<tr>
                    <td>${rec.id}</td>
                    <td>${rec.product_id}</td>
                    <td>${rec.customer_id}</td>
                    <td>${rec.product_name}</td>
                    <td>${rec.recommendation_name}</td>
                    <td>${rec.recommend_product_id}</td>
                    <td>${rec.recommend_type}</td>
                    <td>${rec.rec_success}</td>
                </tr>`;
                $("#search_results tbody").append(row);
            }
            flash_message("Success", "success");
        });

        ajax.fail(function(res){
            flash_message("Server error while listing items!", "danger");
        });
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************
    $("#create-btn").click(function () {
        let data = {
            product_id: parseInt($("#product_id").val()),
            customer_id: parseInt($("#customer_id").val()),
            product_name: $("#product_name").val(),
            recommendation_name: $("#recommendation_name").val(),
            recommend_product_id: parseInt($("#recommend_product_id").val()),
            recommend_type: $("#recommend_type").val(),
            rec_success: parseInt($("#rec_success").val())
        };

        flash_message("");

        $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        }).done(function(res){
            update_form_data(res);
            flash_message("Success", "success");
        }).fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************
    $("#retrieve-btn").click(function () {
        let recommendation_id = $("#read_id").val();

        flash_message("");

        $.ajax({
            type: "GET",
            url: `/recommendations/${recommendation_id}`,
            contentType: "application/json",
        }).done(function(res){
            $("#search_results tbody").empty();
            let row = `<tr>
                <td>${res.id}</td>
                <td>${res.product_id}</td>
                <td>${res.customer_id}</td>
                <td>${res.product_name}</td>
                <td>${res.recommendation_name}</td>
                <td>${res.recommend_product_id}</td>
                <td>${res.recommend_type}</td>
                <td>${res.rec_success}</td>
            </tr>`;
            $("#search_results tbody").append(row);
            flash_message("Success", "success");
        }).fail(function(res){
            $("#search_results tbody").empty();
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Search Recommendations with Filters
    // ****************************************
    $("#filter-search-btn").click(function () {
        let query = [];
        let product_id = $("#read_product_id").val();
        let customer_id = $("#read_customer_id").val();
        let recommend_product_id = $("#read_recommend_product_id").val();
        let recommend_type = $("#read_recommend_type").val();
        let product_name = $("#read_product_name").val();
        let recommendation_name = $("#read_recommendation_name").val();
        let rec_success_min = $("#rec_success_min").val();
        let rec_success_max = $("#rec_success_max").val();
    
        if (product_id) query.push(`product_id=${product_id}`);
        if (customer_id) query.push(`customer_id=${customer_id}`);
        if (recommend_product_id) query.push(`recommend_product_id=${recommend_product_id}`);
        if (recommend_type && recommend_type !== "Select" && recommend_type !== "Any") query.push(`recommend_type=${recommend_type}`);
        if (product_name) query.push(`product_name=${product_name}`);
        if (recommendation_name) query.push(`recommendation_name=${recommendation_name}`);
        if (rec_success_min && rec_success_max) {
            let minVal = parseInt(rec_success_min);
            let maxVal = parseInt(rec_success_max);
        
            if (isNaN(minVal) || isNaN(maxVal)) {
                flash_message("Please enter valid numeric values for success rate range.", "warning");
                return;
            }
        
            if (minVal > maxVal) {
                flash_message("Why is the minimum greater than the maximum?", "warning");
                return;
            }
        
            query.push(`rec_success_min=${minVal}`);
            query.push(`rec_success_max=${maxVal}`);
        } else if (rec_success_min || rec_success_max) {
            flash_message("Please enter both minimum and maximum values.", "warning");
            return;
        }
        
        
    
        let queryString = query.length > 0 ? `?${query.join("&")}` : "";
    
        flash_message("");
    
        $.ajax({
            type: "GET",
            url: `/recommendations${queryString}`,
            contentType: "application/json",
        }).done(function(res){
            $("#search_results tbody").empty();
            for (let rec of res) {
                let row = `<tr>
                    <td>${rec.id}</td>
                    <td>${rec.product_id}</td>
                    <td>${rec.customer_id}</td>
                    <td>${rec.product_name}</td>
                    <td>${rec.recommendation_name}</td>
                    <td>${rec.recommend_product_id}</td>
                    <td>${rec.recommend_type}</td>
                    <td>${rec.rec_success}</td>
                </tr>`;
                $("#search_results tbody").append(row);
            }
            flash_message("Success", "success");
        }).fail(function(res){
            $("#search_results tbody").empty();
            flash_message(res.responseJSON.message);
        });
    });    

    // ****************************************
    // Update a Recommendation
    // ****************************************
    $("#update-btn").click(function () {
        let id = $("#update_id").val().trim();
        if (!id) {
            flash_message("Please enter a valid ID to update.", "warning");
            return;
        }

        let data = {};
        let product_id = $("#update_product_id").val().trim();
        let customer_id = $("#update_customer_id").val().trim();
        let product_name = $("#update_product_name").val().trim();
        let recommendation_name = $("#update_recommendation_name").val().trim();
        let recommend_product_id = $("#update_recommend_product_id").val().trim();
        let recommend_type = $("#update_recommend_type").val();
        let rec_success = $("#update_rec_success").val().trim();

        if (product_id !== "") data.product_id = parseInt(product_id);
        if (customer_id !== "") data.customer_id = parseInt(customer_id);
        if (product_name !== "") data.product_name = product_name;
        if (recommendation_name !== "") data.recommendation_name = recommendation_name;
        if (recommend_product_id !== "") data.recommend_product_id = parseInt(recommend_product_id);
        if (recommend_type !== "" && recommend_type !== "Select") data.recommend_type = recommend_type;
        if (rec_success !== "") data.rec_success = parseInt(rec_success);

        flash_message("");

        $.ajax({
            type: "PUT",
            url: `/recommendations/${id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        }).done(function(res){
            flash_message("Update success!", "success");
        }).fail(function(res){
            flash_message(res.responseJSON.message || "Update failed.");
        });
    });

    // ****************************************
    // Delete a Recommendation by ID
    // ****************************************
    $("#delete-id-btn").click(function () {
        let id = $("#delete_id").val();

        flash_message("");

        $.ajax({
            type: "DELETE",
            url: `/recommendations/${id}`,
            contentType: "application/json",
        }).done(function(res){
            $("#delete_id").val("");
            flash_message("Recommendation deleted successfully.", "success");
        }).fail(function(res){
            flash_message("Delete failed! Could not find recommendation.", "danger");
        });
    });

    // ****************************************
    // Clear Buttons
    // ****************************************
    $("#clear-btn").click(function () {
        flash_message("");
        clear_form_data();
    });

    $("#clear-read-btn").click(function () {
        $("#read_id").val("");
        $("#read_product_id").val("");
        $("#read_customer_id").val("");
        $("#read_recommend_product_id").val("");
        $("#read_recommend_type").val("Select");
        $("#read_product_name").val("");
        $("#read_recommendation_name").val("");
        $("#read_rec_success").val("");
        $("#flash_message").empty();
        $("#search_results tbody").empty();
    });    

    $("#clear-update-btn").click(function () {
        $("#update_id").val("");
        $("#update_product_id").val("");
        $("#update_customer_id").val("");
        $("#update_product_name").val("");
        $("#update_recommendation_name").val("");
        $("#update_recommend_product_id").val("");
        $("#update_recommend_type").val("Select");
        $("#update_rec_success").val("");
        $("#flash_message").empty();
        $("#search_results tbody").empty();
    });

    $("#clear-delete-btn").click(function () {
        $("#delete_id").val("");
        flash_message("");
    });

    // ****************************************
    // List Buttons
    // ****************************************
    $("#list-btn").click(listAllRecommendations);
    $("#list-read-btn").click(listAllRecommendations);
    $("#list-update-btn").click(listAllRecommendations);
    $("#list-delete-btn").click(listAllRecommendations);

});