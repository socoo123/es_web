package dev.esweb.travel;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import tools.jackson.core.JsonParser;
import tools.jackson.core.JsonToken;
import tools.jackson.databind.DeserializationContext;
import tools.jackson.databind.ValueDeserializer;
import tools.jackson.databind.annotation.JsonDeserialize;

public record HotelRankingInput(
        @NotNull @Pattern(regexp="西湖|运河") String q,
        @NotNull @Pattern(regexp="relevance|quality|distance") String hotelSort,
        @NotNull @Pattern(regexp="total|preferred") String roomSort,
        @NotNull @JsonDeserialize(using=StrictBoolean.class) Boolean requireBreakfast,
        @NotNull @JsonDeserialize(using=StrictBoolean.class) Boolean requireFlexible,
        @NotNull @Pattern(regexp="all|top2") String scope) {
    public static class StrictBoolean extends ValueDeserializer<Boolean> {
        @Override public Boolean deserialize(JsonParser parser, DeserializationContext context) {
            if(parser.currentToken()==JsonToken.VALUE_TRUE)return true;
            if(parser.currentToken()==JsonToken.VALUE_FALSE)return false;
            return context.reportInputMismatch(Boolean.class,"Expected a JSON boolean");
        }
    }
}
