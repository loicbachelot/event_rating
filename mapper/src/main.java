/**
 * Created by mady on 14/01/18.
 *
 * @author mady
 */

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mongodb.*;

import java.net.UnknownHostException;

import static java.lang.Thread.sleep;

public class main {

    public static String getlocation(String file) {
        JsonElement jelement = new JsonParser().parse(file);
        JsonObject jobject = jelement.getAsJsonObject();
/*        System.out.println(jobject + " \n ok \n");
        JsonArray jarray = jobject.getAsJsonArray("coordinates");

        System.out.println(jarray + " \n ok \n");*/
        JsonElement nestedElement = jobject.get("coordinates");
        jobject = nestedElement.getAsJsonObject();
        JsonElement coordinates = jobject.get("coordinates");

        JsonArray array = coordinates.getAsJsonArray();
        String lat = array.get(0).toString();
        String lon = array.get(1).toString();
        return (lat + "\t" + lon);
    }

    public static void main(String[] args) {

        try {

            Mongo mongo = new Mongo("192.168.1.9", 27017);
            DB db = mongo.getDB("tweeter");

            // get a single collection
            DBCollection collection = db.getCollection("tweets");
            int a = 0;
            while (a == 0) {
                System.out.println("\n1. Find all matched documents " + collection.count());
                BasicDBObject allQuery = new BasicDBObject();
                BasicDBObject fields = new BasicDBObject();
                fields.put("coordinates", 1);

                DBCursor cursor = collection.find(allQuery, fields);

                while (cursor.hasNext()) {
                    String file = cursor.next().toString();
                    //System.out.println(file);
                    if (!file.contains("null")) {
                        System.out.println(getlocation(file));
                    }
                }
                sleep(3000);


            }


/*
            System.out.println("\n1. Get 'name' field only");
            BasicDBObject allQuery = new BasicDBObject();
            BasicDBObject fields = new BasicDBObject();
            fields.put("name", 1);

            DBCursor cursor2 = collection.find(allQuery, fields);
            while (cursor2.hasNext()) {
                System.out.println(cursor2.next());
            }

            System.out.println("\n2. Find where number = 5");
            BasicDBObject whereQuery = new BasicDBObject();
            whereQuery.put("number", 5);
            DBCursor cursor3 = collection.find(whereQuery);
            while (cursor3.hasNext()) {
                System.out.println(cursor3.next());
            }

            System.out.println("\n2. Find where number in 2,4 and 5");
            BasicDBObject inQuery = new BasicDBObject();
            List<Integer> list = new ArrayList<Integer>();
            list.add(2);
            list.add(4);
            list.add(5);
            inQuery.put("number", new BasicDBObject("$in", list));
            DBCursor cursor4 = collection.find(inQuery);
            while (cursor4.hasNext()) {
                System.out.println(cursor4.next());
            }

            System.out.println("\n2. Find where 5 > number > 2");
            BasicDBObject gtQuery = new BasicDBObject();
            gtQuery.put("number", new BasicDBObject("$gt", 2).append("$lt", 5));
            DBCursor cursor5 = collection.find(gtQuery);
            while (cursor5.hasNext()) {
                System.out.println(cursor5.next());
            }

            System.out.println("\n2. Find where number != 4");
            BasicDBObject neQuery = new BasicDBObject();
            neQuery.put("number", new BasicDBObject("$ne", 4));
            DBCursor cursor6 = collection.find(neQuery);
            while (cursor6.hasNext()) {
                System.out.println(cursor6.next());
            }

            System.out.println("\n3. Find when number = 2 and name = 'mkyong-2' example");
            BasicDBObject andQuery = new BasicDBObject();

            List<BasicDBObject> obj = new ArrayList<BasicDBObject>();
            obj.add(new BasicDBObject("number", 2));
            obj.add(new BasicDBObject("name", "mkyong-2"));
            andQuery.put("$and", obj);

            System.out.println(andQuery.toString());

            DBCursor cursor7 = collection.find(andQuery);
            while (cursor7.hasNext()) {
                System.out.println(cursor7.next());
            }

            System.out.println("\n4. Find where name = 'Mky.*-[1-3]', case sensitive example");
            BasicDBObject regexQuery = new BasicDBObject();
            regexQuery.put("name",
                    new BasicDBObject("$regex", "Mky.*-[1-3]")
                            .append("$options", "i"));

            System.out.println(regexQuery.toString());

            DBCursor cursor8 = collection.find(regexQuery);
            while (cursor8.hasNext()) {
                System.out.println(cursor8.next());
            }

            collection.drop();

            System.out.println("Done");
*/
        } catch (UnknownHostException e) {
            e.printStackTrace();
        } catch (MongoException e) {
            e.printStackTrace();

        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }
}
