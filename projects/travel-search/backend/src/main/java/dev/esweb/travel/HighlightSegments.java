package dev.esweb.travel;

import java.util.ArrayList;
import java.util.List;
import org.springframework.web.util.HtmlUtils;

/** Only literal server-controlled mark delimiters are structural; decode text after splitting. */
public final class HighlightSegments {
    private HighlightSegments() {
    }

    public static List<MultiFieldResult.Segment> parse(String encoded) {
        var parts = new ArrayList<MultiFieldResult.Segment>();
        int cursor = 0;
        boolean matched = false;
        while (cursor < encoded.length()) {
            String delimiter = matched ? "</mark>" : "<mark>";
            int next = encoded.indexOf(delimiter, cursor);
            int end = next < 0 ? encoded.length() : next;
            String text = encoded.substring(cursor, end);
            // encoder=html escapes original markup. Any other literal bracket is outside our contract.
            if (text.contains("<") || text.contains(">") || (matched && next < 0)) {
                throw new AttractionSearchService.IncompleteSearchException();
            }
            if (!text.isEmpty()) parts.add(new MultiFieldResult.Segment(HtmlUtils.htmlUnescape(text), matched));
            if (next < 0) break;
            matched = !matched;
            cursor = next + delimiter.length();
        }
        if (matched) throw new AttractionSearchService.IncompleteSearchException();
        return List.copyOf(parts);
    }

    public static MultiFieldResult.Snippet snippet(String field, List<String> fragments, String fallback) {
        if (fragments == null || fragments.isEmpty()) {
            return new MultiFieldResult.Snippet(field, false,
                    List.of(new MultiFieldResult.Segment(fallback, false)));
        }
        var segments = new ArrayList<MultiFieldResult.Segment>();
        for (String fragment : fragments) {
            if (!segments.isEmpty()) segments.add(new MultiFieldResult.Segment(" … ", false));
            segments.addAll(parse(fragment));
        }
        return new MultiFieldResult.Snippet(field, true, List.copyOf(segments));
    }
}
